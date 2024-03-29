package com.comp6239.Student;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.comp6239.Backend.Model.Tutor;
import com.comp6239.R;
import com.comp6239.Student.StudentSearchTutorsFragment.OnSearchTutorFragmentInteractionListener;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link } and makes a call to the
 * specified {@link OnSearchTutorFragmentInteractionListener}.
 * TODO: Replace the implementation with code for your data type.
 */
public class SearchTutorRecyclerViewAdapter extends RecyclerView.Adapter<SearchTutorRecyclerViewAdapter.ViewHolder> {

    private final List<Tutor> mValues;
    private final OnSearchTutorFragmentInteractionListener mListener;

    public SearchTutorRecyclerViewAdapter(List<Tutor> items, OnSearchTutorFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.fragment_tutor_search, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mNameView.setText(mValues.get(position).getFirstName() + " " + mValues.get(position).getLastName());
        if(mValues.get(position).getPrice() != null && mValues.get(position).getSubjects() != null) {
            holder.mPriceView.setText("£" + mValues.get(position).getPrice().toString() + " per hour");
            holder.mNumOfSubjectsView.setText(mValues.get(position).getSubjects().length +" Subject(s)");
        }


        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (null != mListener) {
                    // Notify the active callbacks interface (the activity, if the
                    // fragment is attached to one) that an item has been selected.
                    mListener.onSearchTutorsFragmentInteraction(holder.mItem);
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        if (mValues == null) return 0;
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final View mView;
        public final TextView mNameView;
        public final TextView mPriceView;
        public final TextView mNumOfSubjectsView;
        public Tutor mItem;

        public ViewHolder(View view) {
            super(view);
            mView = view;
            mNameView = view.findViewById(R.id.tutor_name);
            mPriceView = view.findViewById(R.id.tutor_price);
            mNumOfSubjectsView = view.findViewById(R.id.most_recent_message);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mNameView.getText() + "'";
        }
    }
}
